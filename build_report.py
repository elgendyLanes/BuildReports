import getopt

from bs4 import BeautifulSoup
import subprocess
import sys
import os.path


REPORT_PATH = ''

def read_args(argv):
  global REPORT_PATH

  (opts, args) = getopt.getopt(argv, 'h:', [
    'report='
  ])

  for (opt, arg) in opts:
    if opt == '--report':
      REPORT_PATH = arg

  check_required_args(((REPORT_PATH, 'report')))


def check_required_args(arg_value_name_pairs):
  for pair in arg_value_name_pairs:
    if not pair[0]:
      print pair[1], 'is empty or invalid'
      sys.exit(1)


def get_soup(url):
  return BeautifulSoup(open(url), 'html.parser')


def add_header(text):
  file.write("\n\n<h2>" + text + "</h2>\n\n")


def write(text):
  file.write(text)


def runShell(command):
  return subprocess.Popen(
          command,
          shell=True,
          stdout=subprocess.PIPE
        ).stdout.read()


def generate_unit_tests():
  soup = get_soup(REPORT_PATH + "/unittests.html")

  # Add summary
  div_summary = soup.find('div', attrs={'id': 'summary'})
  write(str(div_summary))

  # Tabs are generated dynamically based on the status. For example: If there is no failure test
  # Failure tab won't be shown, therefore we need to dynamically fetch the classes tab which is
  # always the last tab
  tab_links = soup.find('ul', attrs={'class': 'tabLinks'}).find_all('li')
  last_tab = "tab" + str(len(tab_links) - 1)

  # Add test classes
  div_classes = soup.find('div', attrs={'id': last_tab})
  div_classes.h2.extract()

  tr_tags = div_classes.tbody.find_all('tr')
  for tr in tr_tags:
    td_tags = tr.find_all('td')

    # 0 : Empty column, we will replace it with name
    # 1 : Test count
    # 2 : Failure test count
    # 3 : Ignored test count
    # 4 : Duration in second
    # 5 : Status

    for index, item in enumerate(td_tags):
      # There is a bug in the generated report. An empty redundant column is generated.
      # We fix it by removing basically and add the class name as new column
      if index == 0:
        item.extract()

      # If the test class has failures, paint to red
      if index == 2:
        fail_count = float(item.string)
        if fail_count > 0:
          tr['bgcolor'] = "#ff9999"

      # If the test class has ignoring tests, paint to orange
      if index == 3:
        ignore_count = float(item.string)
        if ignore_count > 0:
          tr['bgcolor'] = "#ffeb99"

      # If the duration is longer than 1 second, paint to blue
      if index == 4:
        duration = float(item.string[:-1])
        if duration > 1:
          tr['bgcolor'] = "#ccccff"

  # There is a bug in generated test report html which is class names are not inside <td> tag
  # Remove the links and move them inside a td tag
  links = div_classes.find_all('a')
  for a in links:
    a.wrap(soup.new_tag('td'))
    a.insert_after(str(a.string))
    a.extract()

  write(str(div_classes))


def generate_coverage_report():
  soup = get_soup(REPORT_PATH + "/coveragetests.html")

  # Add test classes
  div_table = soup.find('table', attrs={'id': 'coveragetable'})
  div_table.extract()

  head_tr_tags = div_table.thead.find_all('tr')
  for tr in head_tr_tags:
    head_td_tag = tr.find_all('td')
    for h in head_td_tag:
        h.wrap(soup.new_tag('th',style="background-color:yellow; padding-right:10px"))
        h.insert_after(str(h.string))
        h.extract()

  body_tr_tags = div_table.tbody.find_all('tr')
  for tr in body_tr_tags:
    body_td_tag = tr.find_all('td')

    # 1 : Test count
    # 3 : Ignored test count

    redStyle = "width:{WIDTH}; height:{HEIGHT}; background:red; margin-right:-4px; float:left"
    greenStyle = "width:{WIDTH}; height:{HEIGHT}; background:blue; float:left"
    for index, item in enumerate(body_td_tag):
      if (index == 1) or (index == 3):
          imageTags = item.find_all('img')
          for imageTag in imageTags:
              if imageTag is not None:
                  img_width = imageTag.get('width')
                  img_height = imageTag.get('height')
                  img_title = imageTag.get('title')
                  new_tag = soup.new_tag('div',style=redStyle.format(WIDTH = img_width, HEIGHT = img_height))
                  if "greenbar" in imageTag.get('src'):
                      new_tag = soup.new_tag('div',style=greenStyle.format(WIDTH = img_width, HEIGHT = img_height))

                  #new_tag.append(img_title)
                  item.append(new_tag)
                  imageTag.replaceWithChildren()

  # There is a bug in generated test report html which is class names are not inside <td> tag
  # Remove the links and move them inside a td tag
  links = div_table.find_all('a')
  for a in links:
    a.replaceWithChildren()

  write(str(div_table))

if __name__ == '__main__':
  read_args(sys.argv[1:])


with open(REPORT_PATH + '/build-report.html', 'w+') as file:
  print "Generating pull request info"
  write('<html lang="en"><head><meta charset="UTF-8"></head><body>')

  print "Generating unit test report"
  add_header("Unit Tests")
  generate_unit_tests()

  #jacoco-part
  print "Generating coverage test report"
  add_header("Coverage Report")
  generate_coverage_report()

  print "Build report is generated at " + REPORT_PATH + "/build-report.html"
  write('</body></html>')
